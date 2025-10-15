program1
# Create simulator
set ns [new Simulator]
set nt [open lab1.tr w]
set nf [open lab1.nam w]
$ns trace-all $nt
$ns namtrace-all $nf

# Nodes
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

# Links (bw delay queue)
$ns duplex-link $n0 $n2 10Mb 300ms DropTail
$ns duplex-link $n1 $n2 10Mb 300ms DropTail
$ns duplex-link $n2 $n3 100Kb 300ms DropTail

# Queue limit
$ns queue-limit $n2 $n3 5

# Agents
set udp0 [new Agent/UDP]
set udp1 [new Agent/UDP]
set null3 [new Agent/Null]

$ns attach-agent $n0 $udp0
$ns attach-agent $n1 $udp1
$ns attach-agent $n3 $null3

# CBR traffic
set cbr0 [new Application/Traffic/CBR]
$cbr0 attach-agent $udp0
set cbr1 [new Application/Traffic/CBR]
$cbr1 attach-agent $udp1

$ns connect $udp0 $null3
$ns connect $udp1 $null3

# Packet size and interval
$cbr0 set packetSize_ 500
$cbr0 set interval_ 0.005
$cbr1 set packetSize_ 500
$cbr1 set interval_ 0.005

# Finish
proc finish {} {
    global ns nf nt
    $ns flush-trace
    close $nt
    close $nf
    exec nam lab1.nam &
    exit 0
}

# Run
$ns at 0.1 "$cbr0 start"
$ns at 0.1 "$cbr1 start"
$ns at 10.0 "finish"
$ns run

BEGIN { count=0 }
{ if ($1=="d") count++ }
END { print "Packets Dropped =", count }


ns lab1.tcl          # Run simulation
nam lab1.nam         # Open animation
awk -f drop.awk lab1.tr   # Show dropped packets




program5
import java.util.*;

public class SlidingWindow {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("No. of frames: ");
        int n = sc.nextInt();
        System.out.print("Window size: ");
        int w = sc.nextInt();
        int sent = 0, ack = 0;
        Random r = new Random();

        while (ack < n) {
            for (int i = 0; i < w && sent < n; i++)
                System.out.println("Sending frame " + sent++);
            for (int i = 0; i < w && ack < n; i++) {
                if (r.nextInt(10) > 1)
                    System.out.println("Ack for frame " + ack++);
                else {
                    System.out.println("Frame " + ack + " lost, resend...");
                    sent = ack;
                    break;
                }
            }
        }
        System.out.println("All frames sent!");
        sc.close();
    }
}

//run command
javac SlidingWindow.java
java SlidingWindow



program4

import java.util.*;

public class CRC {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter Dataword: ");
        String data = sc.next();
        System.out.print("Enter Divisor: ");
        String div = sc.next();

        // Append zeros (length = divisor - 1)
        String appended = data + "0".repeat(div.length() - 1);

        // Find remainder (CRC bits)
        String rem = mod2div(appended, div);
        String codeword = data + rem;
        System.out.println("Codeword: " + codeword);

        // Check received code
        System.out.print("Enter Received Codeword: ");
        String recv = sc.next();
        if (mod2div(recv, div).contains("1"))
            System.out.println("Error detected!");
        else
            System.out.println("No error detected.");
        sc.close();
    }

    // Performs Mod-2 Division
    static String mod2div(String dividend, String divisor) {
        int len = divisor.length();
        String tmp = dividend.substring(0, len);
        for (int i = len; i < dividend.length(); i++) {
            tmp = tmp.charAt(0) == '1' ? xor(divisor, tmp) : xor("0".repeat(len), tmp);
            tmp = tmp.substring(1) + dividend.charAt(i);
        }
        tmp = tmp.charAt(0) == '1' ? xor(divisor, tmp) : xor("0".repeat(len), tmp);
        return tmp.substring(1);
    }

    // XOR operation between two strings
    static String xor(String a, String b) {
        StringBuilder res = new StringBuilder();
        for (int i = 0; i < b.length(); i++)
            res.append(a.charAt(i) == b.charAt(i) ? '0' : '1');
        return res.toString();
    }
}

//runcommand
ns Lab4.tcl
awk -f Lab4.awk Lab4.tr
!pip install -q langgraph google-genai

import os
from datetime import datetime
from typing import TypedDict
from langgraph.graph import StateGraph, END
from google import genai


os.environ["GOOGLE_API_KEY"] = "AIzaSyDtXa3YdxH2OQWElswgqCkWt4ODhOhL6kQ"

client = genai.Client()

class ResearchState(TypedDict):
    user_query: str
    response: str
    reference_link: str
    current_step: str

# ✈️ Flight rate checker
def flight_rate_agent(state: ResearchState) -> ResearchState:
    print("✈️ Searching for flight rate info (Gemini-based)...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            You are a travel assistant.
            Estimate the typical flight prices for this request:
            "{state['user_query']}"

            Include:
            - Major airlines operating this route
            - Approximate price range (economy class)
            - Notes on factors affecting price (e.g., booking time, airlines)
            Use realistic, region-appropriate values.
            Also include a link to a reputable travel booking site for more information.
            """
        )
        output = response.text.strip()
        lines = output.splitlines()
    
        link = ""
        for line in reversed(lines):
            if line.startswith("http"):
                link = line
                lines.remove(line)
                break
        state['response'] = "\n".join(lines)
        state['reference_link'] = link
    except Exception as e:
        state['response'] = f"Error fetching flight rates: {e}"
        state['reference_link'] = ""
    state['current_step'] = "completed"
    return state


def date_agent(state: ResearchState) -> ResearchState:
    now = datetime.now()
    formatted = now.strftime("%A, %d %B %Y, %I:%M %p")
    state['response'] = f"📅 Today's date and time: {formatted}"
    
    state['reference_link'] = "https://www.timeanddate.com/worldclock/"
    state['current_step'] = "completed"
    return state


def google_research_agent(state: ResearchState) -> ResearchState:
    print("🔍 Performing research (Gemini model)...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            You are a helpful research assistant.
            Answer the following query in detail:
            "{state['user_query']}"

            Include relevant facts, data, or summaries from your knowledge base.
            Include a link to a reputable website where the user can learn more.
            Write clearly and concisely.
            """
        )
        output = response.text.strip()
        lines = output.splitlines()
        # Try to extract link from last line, if present
        link = ""
        for line in reversed(lines):
            if line.startswith("http"):
                link = line
                lines.remove(line)
                break
        state['response'] = "\n".join(lines)
        state['reference_link'] = link
    except Exception as e:
        state['response'] = f"Error fetching information: {e}"
        state['reference_link'] = ""
    state['current_step'] = "completed"
    return state


def reflection_agent(state: ResearchState) -> ResearchState:
    print("🪞 Reflecting on previous answer...")
    try:
        review_prompt = f"""
        You are an expert reviewer.
        Review the following answer and associated website link for correctness, completeness, clarity, and possible improvements:
        -----ANSWER-----
        {state['response']}
        -----LINK-----
        {state['reference_link']}
        If you find issues, rewrite and improve the answer; for the link, provide a better one if available or confirm it is suitable.
        Respond with the improved answer followed by a website link on its own single line.
        """
        reflection = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=review_prompt
        )
        output = reflection.text.strip()
        lines = output.splitlines()
 
        link = ""
        for line in reversed(lines):
            if line.startswith("http"):
                link = line
                lines.remove(line)
                break
        state['response'] = "\n".join(lines)
        state['reference_link'] = link if link else state['reference_link']
    except Exception as e:
        state['response'] += f"\n(Reflection error: {e})"
    state['current_step'] = "reflected"
    return state


def router(state: ResearchState) -> str:
    query = state['user_query'].lower()
    if "flight" in query and ("rate" in query or "price" in query or "ticket" in query):
        return "flight_agent"
    elif "date" in query or "today" in query or "time" in query:
        return "date_agent"
    else:
        return "google_agent"


def build_multi_agent():
    builder = StateGraph(ResearchState)

    # Add nodes
    builder.add_node("router", lambda s: s)
    builder.add_node("flight_agent", flight_rate_agent)
    builder.add_node("date_agent", date_agent)
    builder.add_node("google_agent", google_research_agent)
    builder.add_node("reflection_agent", reflection_agent)

    # Entry point
    builder.set_entry_point("router")

    # Route main agents based on query
    builder.add_conditional_edges(
        "router",
        router,
        {
            "flight_agent": "flight_agent",
            "date_agent": "date_agent",
            "google_agent": "google_agent",
        },
    )

    builder.add_edge("flight_agent", "reflection_agent")
    builder.add_edge("date_agent", "reflection_agent")
    builder.add_edge("google_agent", "reflection_agent")
    builder.add_edge("reflection_agent", END)

    return builder.compile()


def run_chat_agent():
    print("🤖 GOOGLE MULTI-TOOL AI AGENT READY")
    print("=" * 50)
    print("Ask me anything — research topics")
    print("Type 'exit' to quit.\n")

    agent = build_multi_agent()

    while True:
        user_input = input("🧑‍💻 You: ").strip()
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("👋 Goodbye!")
            break

        state = ResearchState(user_query=user_input, response="", reference_link="", current_step="started")
        result = agent.invoke(state)

        print(f"\n🤖 Agent: {result['response']}")
        if result['reference_link']:
            print(f"🔗 More info: {result['reference_link']}")
        print("-" * 50)

# 🚀 Run
if __name__ == "__main__":
    run_chat_agent()


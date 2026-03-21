# 10-Minute Video Script

This file contains a full timestamped script for the final project video.

It is written to be easy to use for:

- AI voice generation
- slide-based editing
- screen-recording overlays
- prerecorded demo clip assembly

Recommended delivery style:

- narration speed: `0.95x` to `1.0x`
- most explanatory sections: slide or screen recording
- proof sections: prerecorded live demo clips

---

## Existing Assets Already Available

Physical setup:

- [../pictures and videos/full_hardware.jpg](../pictures%20and%20videos/full_hardware.jpg)
- [../pictures and videos/camera.jpg](../pictures%20and%20videos/camera.jpg)
- [../pictures and videos/wand.jpg](../pictures%20and%20videos/wand.jpg)

Dashboard / software:

- [../pictures and videos/higher_website.png](../pictures%20and%20videos/higher_website.png)
- [../pictures and videos/Lower_website.png](../pictures%20and%20videos/Lower_website.png)
- [../pictures and videos/brain_snaphot.mp4](../pictures%20and%20videos/brain_snaphot.mp4)
- [../pictures and videos/state_debug.mp4](../pictures%20and%20videos/state_debug.mp4)

Demo clips:

- [../pictures and videos/double.mp4](../pictures%20and%20videos/double.mp4)
- [../pictures and videos/live_camera_centroid - Jupyter Notebook - Google Chrome 2026-03-21 16-04-52.mp4](../pictures%20and%20videos/live_camera_centroid%20-%20Jupyter%20Notebook%20-%20Google%20Chrome%202026-03-21%2016-04-52.mp4)

Diagnostics:

- [../pictures and videos/web_connection_test.png](../pictures%20and%20videos/web_connection_test.png)
- [../pictures and videos/camera_availability_test.png](../pictures%20and%20videos/camera_availability_test.png)

FPGA visuals:

- [../../FPGA/designs/centroid_pipeline/used_version/images/top.png](../../FPGA/designs/centroid_pipeline/used_version/images/top.png)
- [../../FPGA/designs/centroid_pipeline/used_version/images/timing.png](../../FPGA/designs/centroid_pipeline/used_version/images/timing.png)

---

## Timestamped Script

### 0:00-0:35

**Suggested background**

- title slide
- [../pictures and videos/full_hardware.jpg](../pictures%20and%20videos/full_hardware.jpg)

**Voiceover**

This project is an FPGA-based multi-node interactive drawing system. Each node
performs local processing on a PYNQ board, observes an illuminated wand through
a camera, and sends compact drawing events to a cloud service. The cloud
service, called Wand Brain, reconstructs strokes, visualizes them live, scores
finalized attempts against templates, and stores the results. The final system
supports two nodes, bidirectional communication, live monitoring, and
leaderboard-based gameplay features.

---

### 0:35-1:20

**Suggested background**

- architecture slide
- simple animation showing node, cloud, browser, and control/data arrows

**Voiceover**

The system is organized into two main parts: the local node and the cloud
backend. On each node, a camera captures the wand motion, and the PYNQ board
performs the first stage of processing locally. The cloud backend receives
point events over UDP, reconstructs the drawing attempt, renders the live and
finalized stroke, evaluates it against the selected template, and serves a
browser dashboard over HTTP. A separate HTTP control path allows the server to
send settings back to the node, so the local runtime can be influenced
dynamically during operation.

---

### 1:20-2:20

**Suggested background**

- [../pictures and videos/camera.jpg](../pictures%20and%20videos/camera.jpg)
- [../pictures and videos/wand.jpg](../pictures%20and%20videos/wand.jpg)
- [../../FPGA/designs/centroid_pipeline/used_version/images/top.png](../../FPGA/designs/centroid_pipeline/used_version/images/top.png)

**Voiceover**

On the node side, the processing is split between the Processing System, or
PS, and the Programmable Logic, or PL. The PS captures frames from the camera,
converts them to grayscale, resizes them to six hundred and forty by four
hundred and eighty, applies thresholding, manages DMA transfers, and handles
both UDP and HTTP communication. The PL contains a custom centroid-reduction IP
block. This hardware module scans the thresholded image stream and accumulates
compact statistics: the sum of x positions, the sum of y positions, the
foreground pixel count, a frame identifier, and a valid signal. The PS reads
these values back over AXI-Lite, computes the centroid, and decides whether
that point should be accepted, displayed locally, and transmitted to the
server.

---

### 2:20-3:05

**Suggested background**

- protocol slide
- packet field table for `wb-point-v1`

**Voiceover**

For node-to-server communication, the system uses a fixed-size UDP protocol
called wb-point version one. Each UDP packet carries exactly one point sample
together with device identity, wand identity, packet number, stroke number,
timestamp, and stroke state flags. The packet is only twenty-four bytes long,
which keeps transmission lightweight and suitable for interactive drawing. UDP
was chosen because the system is event-driven and low latency matters more than
guaranteed retransmission. HTTP is used separately for health checks, node
control, acknowledgements, and the browser dashboard.

---

### 3:05-4:00

**Suggested background**

- [../pictures and videos/brain_snaphot.mp4](../pictures%20and%20videos/brain_snaphot.mp4)
- dashboard or backend flow slide

**Voiceover**

On the cloud side, the Wand Brain backend receives UDP packets, parses them
into structured point events, groups them into active attempts, and rasterizes
these points into live and finalized images. When a stroke ends, either through
an explicit end event or an idle timeout, the backend finalizes the attempt,
scores it against the currently selected template, and stores the result in the
database. The backend is also responsible for serving health endpoints,
template APIs, leaderboard APIs, and the live dashboard used during the
demonstration.

---

### 4:00-4:45

**Suggested background**

- node control panel screen recording
- [../pictures and videos/state_debug.mp4](../pictures%20and%20videos/state_debug.mp4)

**Voiceover**

A key requirement of the project was that information had to flow from the
server back to the nodes in a way that affects local processing. This is
implemented through HTTP polling from the PYNQ nodes. The server can change
control state such as whether a node is enabled, whether it is armed to start a
stroke, whether transmission is active, and which runtime mode is applied. It
can also adjust threshold-related settings and trigger recalibration. This
means the cloud service is not only receiving data; it is also actively
influencing the node-side runtime.

---

### 4:45-5:50

**Suggested background**

- single-node prerecorded demo clip
- [../pictures and videos/live_camera_centroid - Jupyter Notebook - Google Chrome 2026-03-21 16-04-52.mp4](../pictures%20and%20videos/live_camera_centroid%20-%20Jupyter%20Notebook%20-%20Google%20Chrome%202026-03-21%2016-04-52.mp4)

**Voiceover**

This clip shows the system operating with a single node. As the illuminated
wand moves through the tracked space, the camera captures the motion and the
node reduces each valid frame to a centroid point. Those points are transmitted
to the server over UDP. On the dashboard, the live stroke appears in real time.
Once the stroke is complete, the backend finalizes the attempt, compares it
against the selected template, and records the resulting score. This
demonstrates the complete local-processing, communication, rendering, and
scoring path from end to end.

---

### 5:50-6:55

**Suggested background**

- two-node prerecorded demo clip
- [../pictures and videos/double.mp4](../pictures%20and%20videos/double.mp4)

**Voiceover**

This clip shows the final system operating with two nodes concurrently. Each
node has its own device number and wand identifier, so the backend can separate
the incoming streams and maintain independent attempt state for each one. The
server receives, reconstructs, and displays each wand separately while
preserving live status and finalized history for both. This demonstrates that
the project satisfies the requirement for at least two nodes to both transmit
to and receive from the server within one integrated system.

---

### 6:55-7:45

**Suggested background**

- [../pictures and videos/higher_website.png](../pictures%20and%20videos/higher_website.png)
- [../pictures and videos/Lower_website.png](../pictures%20and%20videos/Lower_website.png)
- [../pictures and videos/brain_snaphot.mp4](../pictures%20and%20videos/brain_snaphot.mp4)

**Voiceover**

Beyond the minimum requirements, additional backend functionality was added to
make the system more complete and more interactive. The dashboard shows recent
attempts, live wand status, finalized scores, and a stroke timer. The database
stores finalized attempts rather than raw packet streams, which keeps the live
path lightweight while preserving useful history. The backend also maintains a
leaderboard for each template, and the highest-scoring player for a template
can claim that result with a name. These features turn the system from a
transport demo into a usable interactive application.

---

### 7:45-8:40

**Suggested background**

- testing flow slide
- [../pictures and videos/web_connection_test.png](../pictures%20and%20videos/web_connection_test.png)
- [../pictures and videos/camera_availability_test.png](../pictures%20and%20videos/camera_availability_test.png)

**Voiceover**

Testing was performed at several levels. First, the backend was validated
through health checks, synthetic UDP injection, and smoke tests for rendering
and finalization. Second, the board-side runtime was validated through camera
bring-up, DMA transfer checks, MMIO readback, and control polling. Finally, the
complete system was tested end to end using real hardware, the deployed EC2
service, and the live dashboard. This included both one-node and two-node
sessions, validation of score generation, recent-attempt updates, leaderboard
behaviour, and server-to-node control.

---

### 8:40-9:30

**Suggested background**

- [../../FPGA/designs/centroid_pipeline/used_version/images/top.png](../../FPGA/designs/centroid_pipeline/used_version/images/top.png)
- [../../FPGA/designs/centroid_pipeline/used_version/images/timing.png](../../FPGA/designs/centroid_pipeline/used_version/images/timing.png)

**Voiceover**

From an FPGA perspective, the final design focuses on accelerating the part of
the pipeline that is most regular and repetitive: scanning the thresholded
image and accumulating foreground statistics. More complex policy logic remains
in software on the PS side. This was a deliberate engineering trade-off. It
kept the hardware design compact and easier to integrate, while still providing
meaningful hardware acceleration. The final adopted PL path achieved timing
closure, which confirms that the chosen implementation was not only functional
but also practical to deploy on the target platform.

---

### 9:30-10:00

**Suggested background**

- closing slide
- [../pictures and videos/full_hardware.jpg](../pictures%20and%20videos/full_hardware.jpg)

**Voiceover**

In summary, this project delivered a complete multi-node FPGA-to-cloud
interactive system with local processing, bidirectional communication, live
visualization, scoring, persistence, and control. The final design combines
hardware acceleration in the FPGA fabric with flexible runtime behaviour in
software and a cloud backend that manages presentation, scoring, and
coordination. The system satisfies the project requirements and also provides a
clear basis for future extensions, including richer tracking, additional
templates, and more advanced game logic.

---

## Editing Notes

- Use slides for architecture, protocol, testing, and conclusion
- Use screen recordings for dashboard, backend behaviour, and node control
- Use prerecorded live clips for single-node and two-node proof sections
- Avoid raw code on screen for more than a few seconds at a time
- If using AI narration, generate section-by-section rather than as one long
  clip so timing is easier to adjust

---

## Suggested Final Export Order

1. title slide
2. architecture slide
3. node-side PS/PL explanation
4. UDP protocol slide
5. backend and dashboard
6. node control
7. single-node live demo
8. two-node live demo
9. leaderboard and persistence
10. testing and validation
11. FPGA timing and design trade-offs
12. closing slide

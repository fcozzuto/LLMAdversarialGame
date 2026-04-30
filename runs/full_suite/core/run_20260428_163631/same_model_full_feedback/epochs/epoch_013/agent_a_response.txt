def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist(a, b, c, d):  # Chebyshev (diagonal allowed)
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # retreat/avoid: prefer moves that increase distance from opponent and stay safe
        best, bestv = [0, 0], -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny): 
                continue
            v = dist(nx, ny, ox, oy)
            # slight bias toward center
            v += -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # pick resource to contest: minimize (my_dist - opp_dist), tie-break closer to me
    best_res = None
    best_key = None
    for rx, ry in resources:
        d_my = dist(sx, sy, rx, ry)
        d_op = dist(ox, oy, rx, ry)
        # Higher opp_dist relative to mine is better; convert to minimization
        key = (d_my - d_op, d_my, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    cur_my = dist(sx, sy, rx, ry)
    # choose move that most reduces my distance to target; if can't, block by increasing opp distance
    best_move, best_score = [0, 0], -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_my = dist(nx, ny, rx, ry)
        d_op_next = dist(nx, ny, ox, oy)  # proxy to deter swapping
        target_progress = cur_my - d_my
        # also consider contesting: prefer moves that make opponent farther from target than me
        d_op_to_target = dist(ox, oy, rx, ry)
        contest = (d_my - d_op_to_target) * 0.5
        score = 100 * target_progress + 0.1 * d_op_next - contest
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move
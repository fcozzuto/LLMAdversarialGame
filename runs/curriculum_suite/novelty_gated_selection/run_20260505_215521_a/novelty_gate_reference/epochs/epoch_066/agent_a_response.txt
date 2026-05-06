def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def clamp_bounds(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()
    best = (None, -10**9)

    # Edge_patrol bias: avoid hugging edges unless it improves resource race.
    def edge_penalty(x, y):
        m = min(x, y, (w - 1) - x, (h - 1) - y)
        if m <= 0: return 5.0
        if m == 1: return 2.0
        return 0.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        nx, ny = clamp_bounds(nx, ny)

        self_best = 10**9
        opp_best = 10**9
        contested = 0
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            if sd < self_best: self_best = sd
            if od < opp_best: opp_best = od
            if sd <= od: contested += 1

        center_bias = (-(abs(nx - cx) + abs(ny - cy)))  # prefer center
        score = (-self_best) + 0.6 * (opp_best) + 0.35 * contested + 0.12 * center_bias - 0.25 * edge_penalty(nx, ny)

        # If we land directly on a resource, strongly prioritize.
        if (nx, ny) in resources:
            score += 1000.0

        if score > best[1]:
            best = ((dx, dy), score)

    return [int(best[0][0]), int(best[0][1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def dist_m(a, b, x, y):
        return abs(a - x) + abs(b - y)

    def score_target(cx, cy, rx, ry):
        od = dist_m(ox, oy, rx, ry)
        cd = dist_m(cx, cy, rx, ry)
        # Prefer targets where we are closer than opponent, with tie-break on closeness
        return (od - cd) + 0.02 * (-(cd + dist_m(ox, oy, cx, cy)))

    best_s = None
    best_m = [0, 0]
    t = int(observation.get("turn_index", 0) or 0)
    parity_flip = (t + sx + sy) & 1

    # Deterministic small bias among ties
    bias_order = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    if parity_flip:
        bias_order = list(reversed(bias_order))

    for dx, dy in bias_order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        s = -10**9
        # Evaluate best deny/converge option among all resources
        for rx, ry in resources:
            s2 = score_target(nx, ny, rx, ry)
            if s2 > s:
                s = s2
        # If we land on a resource, prioritize strongly
        if (nx, ny) in resources:
            s += 10000
        # Subtle preference to keep moving toward the densest part of remaining resources
        s += 0.001 * sum(1 for (rx, ry) in resources if dist_m(nx, ny, rx, ry) <= 2)
        if best_s is None or s > best_s:
            best_s = s
            best_m = [dx, dy]

    return best_m
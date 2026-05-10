def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    # Prefer resources that we can reach first, and also prefer resources "deeper" toward opponent.
    front_dir = 1 if ox > sx else -1
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = man(rx, ry, sx, sy)
        do = man(rx, ry, ox, oy)
        # If opponent is closer, penalize strongly to seek uncontested targets.
        contest = 0
        if do < ds:
            contest = -50 - 5 * (ds - do)
        # Prefer being on the advancing side and aligned in y toward opponent.
        depth = front_dir * (rx - sx)
        align = -abs(ry - oy)
        score = (100 - ds) + contest + 2 * depth + align
        if best is None or score > best_score or (score == best_score and (rx, ry) < best):
            best_score = score
            best = (rx, ry)

    rx, ry = best
    # Greedy step toward target with simple obstacle avoidance + tie-break away from opponent.
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            # distance to chosen resource after move
            d_to = man(nx, ny, rx, ry)
            d_opp = man(nx, ny, ox, oy)
            # prefer closer to target, farther from opponent, and slightly deeper along front_dir
            depth = front_dir * (nx - sx)
            val = (-10 * d_to) + (0.5 * d_opp) + 0.1 * depth
            cand.append((val, dx, dy))
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = cand[0] if cand else (0, 0, 0)
    return [int(dx), int(dy)]
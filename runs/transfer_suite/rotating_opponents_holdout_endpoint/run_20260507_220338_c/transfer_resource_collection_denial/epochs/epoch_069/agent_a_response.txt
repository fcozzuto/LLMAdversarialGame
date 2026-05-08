def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    t = observation.get("turns_remaining", 0)
    t = t if isinstance(t, int) else int(t or 0)

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resset.add((p[0], p[1]))

    if (sx, sy) in resset:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose a resource we can reach earlier than the opponent; if none, pick one with best advantage.
    best = None
    best_key = None
    for rx, ry in resset:
        if (rx, ry) in obst:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Time-weight: commit more strongly as turns get low.
        urgency = 1.0 + (64 - min(64, max(0, t))) / 64.0
        advantage = od - sd
        # If we can beat them, prioritize larger advantage and lower distance.
        key = (advantage * urgency, -sd, -(rx + 2 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy move toward target with obstacle avoidance; consider 8 dirs + stay, deterministic tie-break.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Tie-break order favors diagonal progress then straight.
    dirs.sort(key=lambda d: (abs(d[0]) + abs(d[1]) != 2, abs(d[0]) + abs(d[1]) , d[0], d[1]))

    bestmv = [0, 0]
    bestsc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # Prefer reducing distance to target.
        dnow = man(nx, ny, tx, ty)
        # Also discourage giving opponent a "too-close" lane: if a move makes opponent closer to the same target.
        d_opp = man(ox, oy, tx, ty)
        opp_pen = 0
        if dnow > 0:
            opp_pen = 0.01 * (man(ox, oy, tx, ty) - d_opp)  # deterministic near-zero
        sc = (-dnow, -(abs(nx - tx) + abs(ny - ty)), opp_pen, -((nx + 3 * ny) % 7))
        if bestsc is None or sc > bestsc:
            bestsc = sc
            bestmv = [dx, dy]

    # If all moves blocked (unlikely), stay.
    return bestmv
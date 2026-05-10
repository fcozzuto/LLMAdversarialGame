def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = observation.get("self_role") or "pursuer"
    evader = str(role).lower() == "evader"

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # small tie-breakers to keep deterministic movement preference
        # prioritize moving directly (reduce abs(dx/dy) impact) for pursuer; opposite for evader
        directness = abs(dx) + abs(dy) * 0.01
        if evader:
            val = (d2, directness)
            if best is None or val > best_val:
                best, best_val = [dx, dy], val
        else:
            val = (-d2, -directness)  # minimize d2; then prefer less "detour"
            if best is None or val > best_val:
                best, best_val = [dx, dy], val

    if best is None:
        return [0, 0]
    return best
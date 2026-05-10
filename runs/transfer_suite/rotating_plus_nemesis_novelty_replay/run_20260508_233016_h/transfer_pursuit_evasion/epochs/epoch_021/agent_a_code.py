def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = observation.get("self_role", "pursuer") or "pursuer"

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        if role == "evader":
            val = dist2(nx, ny, ox, oy)  # maximize
        else:
            val = -dist2(nx, ny, ox, oy)  # minimize distance => maximize negative
        candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic tie-break: prefer higher val, then lexicographic (dx, dy)
    best = None
    for c in candidates:
        if best is None:
            best = c
        else:
            if c[0] > best[0]:
                best = c
            elif c[0] == best[0]:
                if (c[1], c[2]) > (best[1], best[2]):
                    best = c
    return [int(best[1]), int(best[2])]
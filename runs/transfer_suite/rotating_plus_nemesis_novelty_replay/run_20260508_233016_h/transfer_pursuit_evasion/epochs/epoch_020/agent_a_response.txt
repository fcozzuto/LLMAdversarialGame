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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    role = observation.get("self_role") or "pursuer"
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Primary desired direction: toward/away from opponent
    if role == "evader":
        tx, ty = sx - (ox - sx), sy - (oy - sy)
    else:
        tx, ty = ox, oy

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue

        # If pursuing: minimize distance. If evading: maximize distance.
        d = dist2(nx, ny, tx, ty)
        # Wall runner / corner cases: lightly prefer moves that increase "freedom"
        # (avoid tight spots) and avoid moving into opponent's exact cell.
        free = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) not in blocked:
                free += 1

        # Deterministic tie-breakers
        # Pursuer prefers smaller distance, then larger freedom, then lexicographically smallest delta.
        # Evader prefers larger distance, then larger freedom, then lexicographically smallest delta.
        if role == "evader":
            val = (-d, -free, dx, dy)
        else:
            val = (d, -free, dx, dy)

        if best is None or val < best_val:
            best = [dx, dy]
            best_val = val

    if best is not None:
        return best

    # Fallback: stay still if no valid move (all blocked/out of bounds)
    return [0, 0]
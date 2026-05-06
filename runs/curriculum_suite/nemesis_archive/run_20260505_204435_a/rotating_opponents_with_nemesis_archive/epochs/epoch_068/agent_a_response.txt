def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        q = None
        if isinstance(r, dict):
            q = r.get("position")
        else:
            q = r
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            x, y = q[0], q[1]
            if inb(x, y) and (x, y) not in blocked:
                rpos.append((x, y))
    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    rpos_sorted = sorted(set(rpos))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Advantage over opponent on the contested resource after moving here.
        best_key = None
        for rx, ry in rpos_sorted:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Prefer resources where we are closer; secondary prefer quicker capture; then deterministic.
            key = (-(od - sd), sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
        # Also lightly discourage moves that let opponent get closer overall (deterministic).
        opp_next = abs(nx - ox) + abs(ny - oy)
        final_key = (best_key[0], best_key[1], best_key[2], best_key[3], opp_next)
        if best is None or final_key < best[0]:
            best = (final_key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]
def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        us = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach at least as fast as opponent; otherwise avoid.
        # Tie-break by smaller us then by position for determinism.
        key = (0 if us <= op else 1, us - op, us, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t
    op_now = cheb(ox, oy, tx, ty)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_v = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_next = cheb(nx, ny, tx, ty)
        # If opponent is already closer to target, prioritize moves that preserve/advance our lead.
        # Penalize stepping away; reward getting closer sharply.
        away = our_next - cheb(sx, sy, tx, ty)
        lead_term = our_next - op_now
        v = our_next * 100 + max(0, lead_term) * 80 + max(0, away) * 20 + (nx * 10 + ny) * 0.001
        if best_v is None or v < best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]
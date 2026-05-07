def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can reach strictly sooner; else still prefer closer relative advantage.
        key = (0 if sd < od else 1, sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # If we are adjacent/at target, still choose move that keeps us on/closest to target.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, tx, ty)  # local tie-break anchor; opponent position affects target selection already
        # Secondary preference: reduce distance to chosen target, then prefer staying in-bounds (already), then deterministic tie.
        key = (d_self, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
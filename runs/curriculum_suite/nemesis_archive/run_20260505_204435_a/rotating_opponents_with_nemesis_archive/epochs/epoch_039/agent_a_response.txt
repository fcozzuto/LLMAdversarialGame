def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked

    def parse_pos(r):
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return (pos[0], pos[1])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    targets = []
    for r in resources:
        p = parse_pos(r)
        if p is not None and legal(p[0], p[1]):
            targets.append(p)

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not targets:
        return [0, 0]

    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Focus: nearest resource to us right now; keep deterministic.
    tx, ty = min(targets, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))

    best_move = (0, 0)
    best_u = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Utility: primarily reduce our distance; secondarily encourage states where opponent is farther.
        # Also lightly penalize stepping into near-obstacle corners to stabilize.
        near_block = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                px, py = nx + ex, ny + ey
                if inb(px, py) and (px, py) in blocked:
                    near_block += 1
        u = (-d_self) + 0.15 * d_opp - 0.02 * near_block

        if best_u is None or u > best_u or (u == best_u and (dx, dy) < best_move):
            best_u = u
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
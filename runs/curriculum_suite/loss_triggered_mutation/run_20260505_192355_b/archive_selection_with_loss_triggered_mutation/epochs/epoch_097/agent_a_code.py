def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a resource that we can reach as well as or better than opponent; break ties toward closer ones.
    best = None
    for tx, ty in targets:
        self_d = cheb((sx, sy), (tx, ty))
        opp_d = cheb((ox, oy), (tx, ty))
        score = (self_d - 1.2 * opp_d, self_d, tx, ty)  # lexicographic
        if best is None or score < best[0]:
            best = (score, (tx, ty))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Try moves that reduce distance to chosen target, avoiding obstacles when possible.
    curd = cheb((sx, sy), (tx, ty))
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            nd = cheb((nx, ny), (tx, ty))
            candidates.append((nd, abs(dx) + abs(dy), dx, dy))
    if candidates:
        # Prefer greatest reduction, then deterministic ordering by (nd, manhattan_step, dx, dy)
        target_list = sorted(candidates, key=lambda t: (t[0] - curd, t[0], t[1], t[2], t[3]))
        nd, _, dx, dy = target_list[0]
        return [int(dx), int(dy)]

    # If completely blocked, attempt any legal move.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]
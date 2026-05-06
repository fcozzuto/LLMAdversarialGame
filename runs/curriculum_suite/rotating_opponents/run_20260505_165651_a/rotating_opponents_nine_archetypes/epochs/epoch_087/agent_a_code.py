def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = r[0], r[1]
            if inb(tx, ty) and (tx, ty) not in obs:
                dme = man(sx, sy, tx, ty)
                dome = man(ox, oy, tx, ty)
                if dme == 0:
                    return [0, 0]
                # Prefer resources opponent is relatively far from (safe steal),
                # but still closer than opponent by some margin.
                steal = (dome - dme) * 2.0
                # Small bias to finish sooner and avoid moving toward opponent directly.
                bias = -0.15 * dme
                alignment = 0.25 if (tx == ox or ty == oy) else 0.0
                diag_align = 0.12 if (tx + ty == ox + oy or tx - ty == ox - oy) else 0.0
                # Deterministic tiebreak using coordinates
                score = steal + bias + alignment + diag_align - 0.0001 * (tx * 8 + ty)
                targets.append((score, dme, dome, tx, ty))
    if not targets:
        return [0, 0]

    targets.sort(reverse=True)
    _, _, _, tx, ty = targets[0]

    # Move one step toward target, but deterministically avoid blocked squares.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # primary: reduce distance to target
        d = man(nx, ny, tx, ty)
        # secondary: don't run into opponent (resource_denier works by denying paths)
        opp_d = man(nx, ny, ox, oy)
        # tertiary: deterministic tie by move order
        key = (-d, opp_d, -(dx * 10 + dy))
        if best is None or key > best[0]:
            best = (key, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]
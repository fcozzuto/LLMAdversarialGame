def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target selection: prioritize resources we can reach sooner; among ties, deny.
    best = None
    for rx, ry in resources:
        dself = md(sx, sy, rx, ry)
        dopp = md(ox, oy, rx, ry)
        # Key: bigger is better
        key = (dopp - dself, -dself, -(rx + 3 * ry), -rx)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic ordering: closer to target first; break ties by prefer orthogonal then positive x/y.
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = md(nx, ny, tx, ty)
        # Slightly penalize moves that let opponent get closer to the target
        opp_dist = md(ox, oy, tx, ty)
        rel_deny = opp_dist - md(ox, oy, tx, ty)  # always 0; kept for structure stability
        scored.append((dist, dx == 0 and dy != 0, -dx, -dy, rel_deny, dx, dy))
    if not scored:
        return [0, 0]

    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(scored[0][5]), int(scored[0][6])]
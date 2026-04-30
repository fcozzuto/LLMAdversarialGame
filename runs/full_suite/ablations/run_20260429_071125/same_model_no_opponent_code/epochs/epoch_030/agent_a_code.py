def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    occ = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        # Choose a target resource considering opponent pressure.
        best_t = None
        best_score = -10**9
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer closer to self, penalize if opponent is closer or equal.
            s = -ds - (0 if do > ds else 3)
            if s > best_score:
                best_score = s
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No resources: move toward center, but keep distance from opponent.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0, -10**9)
    for dx, dy, nx, ny in legal:
        d_to_target = man(nx, ny, tx, ty)
        d_to_opp = man(nx, ny, ox, oy)
        # Maximize: get closer to target; also avoid opponent slightly.
        score = -d_to_target + 0.2 * d_to_opp
        # Deterministic tie-break: prefer non-stay, then lexicographic dx,dy.
        if d_to_target == 0:
            score += 1000
        if score > best_move[2] or (score == best_move[2] and (dx, dy) != (0, 0)):
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Prefer moves that increase opponent distance and keep us central-ish.
            val = (man(nx, ny, ox, oy), -abs(nx - 3.5) - abs(ny - 3.5), -dx, -dy)
            if best is None or val > best:
                best = val
                bestmv = [dx, dy]
        return bestmv

    # Target selection: prioritize denying resources where opponent is closer, but also take winnable ones.
    best_t = None
    for rx, ry in resources:
        d1 = man(sx, sy, rx, ry)
        d2 = man(ox, oy, rx, ry)
        # If we can arrive sooner, strongly favor; otherwise try to reduce their lead.
        # Tie-break toward nearer resources to our position to get moving.
        val = (10 * (d2 - d1) + (-d1) + (d1 == 0), d2 - d1, -d1, -rx - ry)
        if best_t is None or val > best_t:
            best_t = val
            tx, ty = rx, ry

    # Step choice: move toward target; if that would allow opponent much closer, bias to defensive step.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dn = man(nx, ny, tx, ty)
        do = man(ox, oy, tx, ty)
        # After opponent next move (upper bound), estimate if we stay ahead; maximize safety.
        opp_next_lb = do - 1  # opponent can reduce man distance by at most 1 in one step
        ahead = (opp_next_lb - dn)  # higher => we are relatively closer than opponent
        # Also consider moving to increase distance from opponent in general.
        val = (ahead, -dn, man(nx, ny, ox, oy), -abs(dx) - abs(dy), -dx, -dy)
        if best is None or val > best:
            best = val
            bestmv = [dx, dy]
    return bestmv
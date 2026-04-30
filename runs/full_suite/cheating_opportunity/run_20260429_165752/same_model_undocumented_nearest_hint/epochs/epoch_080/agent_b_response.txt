def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if resources:
        # choose a target giving us maximum lead right now, deterministic tie-break by distance sum
        best_r = None
        best_adv = -10**9
        best_tieb = None
        for rx, ry in resources:
            d_s = cheb(sx, sy, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            adv = d_o - d_s
            tieb = (d_s + d_o, rx, ry)
            if adv > best_adv or (adv == best_adv and (best_tieb is None or tieb < best_tieb)):
                best_adv = adv
                best_tieb = tieb
                best_r = (rx, ry)
    else:
        best_r = (W // 2, H // 2)

    rx, ry = best_r
    best_move = (0, 0)
    best_val = -10**18

    # Greedy-on-lead with an extra opponent-separation term to stop being sandwiched
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_our = cheb(nx, ny, rx, ry)

        # Approximate if opponent tries same target next turn: reduce our advantage and increase value when we keep lead
        d_opp = cheb(ox, oy, rx, ry)
        lead = d_opp - d_our

        # discourage moving closer to opponent unless it also improves lead
        d_now_op = cheb(sx, sy, ox, oy)
        d_next_op = cheb(nx, ny, ox, oy)
        sep_bonus = d_next_op - d_now_op  # positive is better separation

        # small obstacle-encouragement: prefer squares with fewer adjacent obstacles (deterministic tie-break naturally)
        adj_obs = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                adj_obs += 1

        val = (2000 * lead) - (3 * d_our) + (20 * sep_bonus) - (1.5 * adj_obs)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []

    # If no resources, move to a safe center while keeping away from opponent.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            score = -md(nx, ny, int(cx), int(cy)) + 0.1 * md(nx, ny, ox, oy)
            candidates.append((score, dx, dy))
        candidates.sort(reverse=True)
        return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]

    # Otherwise: choose move that maximizes (our advantage over opponent) for the most contested resources.
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        opp_d_away = md(nx, ny, ox, oy)
        # Score top few resources by contest advantage.
        advs = []
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # Big positive if we can reach earlier than opponent.
            adv = opp_d - our_d
            advs.append(adv)

        advs.sort(reverse=True)
        k = 3 if len(advs) >= 3 else len(advs)
        top_adv_sum = 0
        for i in range(k):
            top_adv_sum += advs[i]

        # Also slightly prefer moves that don't fall behind on the best resource.
        best_res_d_ours = min(md(nx, ny, rx, ry) for rx, ry in resources)
        score = 10.0 * top_adv_sum - 0.5 * best_res_d_ours + 0.06 * opp_d_away

        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]
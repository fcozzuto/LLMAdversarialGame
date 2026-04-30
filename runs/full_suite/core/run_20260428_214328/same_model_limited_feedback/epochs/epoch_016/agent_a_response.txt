def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    x0, y0 = int(self_pos[0]), int(self_pos[1])
    ox0, oy0 = int(opp_pos[0]), int(opp_pos[1])

    def cheb(a, b):  # steps with 8-neighborhood
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    if not resources:
        # Fallback: drift toward center to reduce collisions with edges/opponent corner trap
        tx, ty = w // 2, h // 2
    else:
        best_r = resources[0]
        best_adv = -10**9
        for r in resources:
            r = (int(r[0]), int(r[1]))
            da = cheb((x0, y0), r)
            db = cheb((ox0, oy0), r)
            adv = db - da
            if adv > best_adv or (adv == best_adv and (da < cheb((x0, y0), best_r))):
                best_adv = adv
                best_r = r
        tx, ty = best_r

    # Choose move that reduces distance to target, prefers staying valid and avoiding obstacles
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    cur_d = cheb((x0, y0), (tx, ty))
    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb((nx, ny), (tx, ty))
        oppd = cheb((ox0, oy0), (nx, ny))
        # Primary: get closer to target; Secondary: avoid moving within 1 step of opponent (reduce contest)
        score = (cur_d - nd) * 1000 - nd - (1 if oppd <= 1 else 0) * 50
        # Tie-break deterministically: lexicographic on deltas for stable behavior
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all non-obstacle moves filtered out, allow staying (engine keeps in place if invalid)
    if best_move == (0, 0) and (x0, y0) in obstacles:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        best = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    cur_to_opp = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_val = -10**18

    # Prefer contested resources: where my distance is <= opponent's distance, then move to reduce my distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dist_me_to_opp = cheb(nx, ny, ox, oy)
        sep_bonus = dist_me_to_opp - cur_to_opp

        best_target_val = -10**18
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dmo = cheb(ox, oy, rx, ry)
            # Contested if I can reach no later than opponent (or close).
            contest = (dmo - dme)
            # Avoid targets that opponent is much closer to.
            reach_pressure = contest
            # Encourage reducing my distance to a contested target.
            my_progress = cheb(sx, sy, rx, ry) - dme
            # Slightly prefer resources that are nearer overall.
            proximity = -dme * 0.05
            val = reach_pressure * 2.0 + my_progress * 1.2 + proximity
            if val > best_target_val:
                best_target_val = val

        # Separation matters to prevent immediate stealing; lightly weight to keep resource pressure primary.
        total = best_target_val + sep_bonus * 0.25 + (dx == 0 and dy == 0) * (-0.05)
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
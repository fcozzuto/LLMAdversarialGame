def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # go to corner that's farthest from opponent
        best_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        tx, ty = best_corner
        # take move that reduces distance to that corner
        best = (0, 0)
        best_d = 10**9
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # choose among closest few resources
    resources_sorted = sorted(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))[:4]
    # evaluate each possible move by (our advantage in time to resources) and safety from opponent
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_dist_to_opp = cheb(nx, ny, ox, oy)
        score = 0
        # consider best target after this move; reward winning that race
        target_best = -10**18
        for rx, ry in resources_sorted:
            my_eta = cheb(nx, ny, rx, ry)
            opp_eta = cheb(ox, oy, rx, ry)
            # positive when we can arrive sooner; also discourage paths where opponent arrives much sooner
            advantage = opp_eta - my_eta
            target_score = 50 * advantage - 2 * my_eta
            # slight bias toward moving toward the resource itself
            target_score += 0.2 * (my_dist_to_opp)
            if target_score > target_best:
                target_best = target_score
        score = target_best + 3 * my_dist_to_opp
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
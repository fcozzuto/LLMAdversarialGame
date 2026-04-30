def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res_list = resources
    if not res_list:
        return [0, 0]

    res_set = set((x, y) for x, y in res_list)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a target resource we are at least as close to as opponent; otherwise minimize opponent lead.
    best_target = res_list[0]
    best_val = -10**18
    for rx, ry in res_list:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        # Primary: margin in our favor. Secondary: closer to the resource.
        val = (od - sd) * 100 - sd
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    cur_d = king_dist(sx, sy, tx, ty)

    def obs_tension(x, y):
        # Penalize adjacency to obstacles (avoid dead corridors).
        t = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in obs:
                t += 1
        return t

    # Evaluate immediate moves toward the chosen target, while explicitly preventing giving the opponent an advantage.
    best_move = [0, 0]
    best_move_score = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue

        hit = 1 if (nx, ny) in res_set else 0
        nd = king_dist(nx, ny, tx, ty)

        # Opponent response estimate: how much closer opponent will be to our target after their next move.
        # (We approximate their next move as their best immediate step; deterministic but local.)
        opp_best = king_dist(ox, oy, tx, ty)
        for kx, ky in moves:
            ax, ay = ox + kx, oy + ky
            if blocked(ax, ay):
                continue
            d = king_dist(ax, ay, tx, ty)
            if d < opp_best:
                opp_best = d

        my_margin = opp_best - nd  # higher means we maintain/extend lead toward target
        # Encourage reducing distance; discourage getting stuck behind obstacles.
        dist_gain = cur_d - nd  # positive is good
        score = 0
        score += hit * 10000
        score += my_margin * 50
        score += dist_gain * 10
        score += -obs_tension(nx, ny) * 3

        # If we land on a non-target resource, slightly prefer it to avoid being too tunnel-visioned.
        if hit and (nx, ny) != (tx, ty):
            score += 50

        if score > best_move_score:
            best_move_score = score
            best_move = [mx, my]

    return best_move
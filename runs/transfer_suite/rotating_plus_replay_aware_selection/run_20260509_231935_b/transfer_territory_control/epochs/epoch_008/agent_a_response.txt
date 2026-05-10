def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    opp_pos = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = {tuple(p) for p in obstacles}

    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    opp_list = list(opp_set) if opp_set else []
    un_list = list(un_set) if un_set else []
    nearest_opp_dist = None
    if opp_list:
        nearest_opp_dist = min(man(sx, sy, ox, oy) for ox, oy in opp_list)
    else:
        nearest_opp_dist = man(sx, sy, opp_pos[0], opp_pos[1])

    # If we're behind, be more aggressive; if ahead, protect frontier.
    self_cnt = observation.get("self_territory_count", len(self_set))
    opp_cnt = observation.get("opponent_territory_count", len(opp_set))
    aggressive = 1.0 if self_cnt <= opp_cnt else 0.6

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0

        if (nx, ny) in opp_set:
            score += 120.0 * aggressive
        if (nx, ny) in un_set:
            score += 22.0
            # Prefer farther expansion toward center of action relative to corners.
            dcen = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            score += 0.15 * dcen

        if (nx, ny) in self_set:
            score += 2.0  # allow mild regrouping

        # Frontier/connection bonus: take cells adjacent to our territory.
        adj_self = 0
        for ax, ay in neigh4:
            if (nx + ax, ny + ay) in self_set:
                adj_self += 1
        score += 6.0 * adj_self

        # Chase opponent territory directionally.
        if opp_list:
            dist = min(man(nx, ny, ox, oy) for ox, oy in opp_list)
        else:
            dist = man(nx, ny, opp_pos[0], opp_pos[1])

        # Use relative improvement compared to current nearest distance.
        improvement = nearest_opp_dist - dist
        score += 8.0 * improvement * aggressive

        # Avoid giving up too much distance when protecting (if ahead).
        if aggressive < 1.0 and improvement < 0:
            score -= 6.0 * (-improvement)

        # Mild obstacle avoidance proxy: don't move adjacent to too many obstacles.
        adj_obs = 0
        for ax, ay in neigh4:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obs:
                adj_obs += 1
        score -= 2.5 * adj_obs

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]
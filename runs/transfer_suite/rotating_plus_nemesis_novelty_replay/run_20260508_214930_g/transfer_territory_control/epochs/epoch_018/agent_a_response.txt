def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    def edge_bonus(nx, ny):
        return (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        target = (nx, ny)
        score = 0

        if target in self_t:
            score += 2 + adj_count(nx, ny, self_t) * 0.5
        elif target in opp_t:
            score += 18 + adj_count(nx, ny, self_t) * 1.0 - adj_count(nx, ny, opp_t) * 0.2
        elif target in unclaimed:
            score += 10 + adj_count(nx, ny, self_t) * 1.0
            score += adj_count(nx, ny, opp_t) * 2.5  # punish edge-claimer by denying their frontier
            score += 3 if edge_bonus(nx, ny) else 0
            score += 0.25 * (0 if target in self_t else 1)

        # Keep compact near opponent by preferring moves that reduce distance to their territory
        if opp_t:
            min_d = 10**9
            for px, py in opp_t:
                d = abs(px - nx) + abs(py - ny)
                if d < min_d:
                    min_d = d
            score += (8 - min_d) * 0.4
        else:
            if edge_bonus(nx, ny):
                score += 1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
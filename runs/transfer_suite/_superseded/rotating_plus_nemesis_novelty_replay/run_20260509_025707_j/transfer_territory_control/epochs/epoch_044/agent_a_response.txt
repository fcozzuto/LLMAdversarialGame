def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = myc < opc

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_cells(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield (nx, ny)

    def adj_opp(x, y):
        for q in adj_cells(x, y):
            if q in opp_set:
                return True
        return False

    contested = [u for u in unclaimed if adj_opp(u[0], u[1])]
    if not contested:
        contested = list(unclaimed)

    def best_dist_from(px, py):
        if not contested:
            return 0
        best = 10**9
        for tx, ty in contested:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        cell = (nx, ny)
        score = 0
        if cell in self_set:
            score += 1
        if cell in unclaimed:
            score += 3 if adj_opp(nx, ny) else 2
        if cell in opp_set:
            score += 6 if behind else 4
        dist = best_dist_from(nx, ny)
        score += -dist * (2.0 if behind else 1.5)
        if adj_opp(nx, ny):
            score += 1.2
        score += -0.05 * (abs(dx) + abs(dy))
        if score > best_score:
            best_score = score
            best_move = (dx if inb(sx + dx, sy + dy) else 0, dy if inb(sx + dx, sy + dy) else 0)
    return [int(best_move[0]), int(best_move[1])]
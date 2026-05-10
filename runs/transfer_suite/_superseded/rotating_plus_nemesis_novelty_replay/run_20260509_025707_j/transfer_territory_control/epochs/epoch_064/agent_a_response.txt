def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    if observation.get("environment_name") != "territory_control":
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False
    def nearest_opp_dist(x, y):
        if not opp_set:
            return 999
        best = 999
        for px, py in opp_set:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # Attack/expand alternation to change behavior profile from pure claimer
    attack_mode = (observation["turn_index"] % 6) in (0, 1, 2)

    # Precompute a small frontier preference: targets adjacent to opponent
    frontier = []
    for ox, oy in opp_set:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny):
                    frontier.append((nx, ny))
    frontier_set = set(frontier)

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        score = 0
        if (nx, ny) in opp_set:
            score += 120  # immediate flip pressure on contact
        if (nx, ny) in unclaimed:
            score += 35  # claim unclaimed when raiding
        if (nx, ny) in self_set:
            score += 8   # holding is safe

        if (nx, ny) in frontier_set:
            score += 18  # actively press opponent frontier

        if attack_mode:
            score += 6 * (9 - nearest_opp_dist(nx, ny))  # approach opponent
            if adj_to_opp(nx, ny) and (nx, ny) not in opp_set:
                score -= 8  # avoid getting squeezed unless we can flip
        else:
            score += 3 * (len(frontier_set) if attack_mode else 1)
            if adj_to_opp(nx, ny):
                score -= 14  # more defensive expansion

        # Deterministic tie-break: prefer staying only if equal, else x then y
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
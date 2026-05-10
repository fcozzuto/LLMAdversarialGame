def choose_move(observation):
    ax, ay = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))
    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))
    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    ox, oy = observation.get("opponent_position", (0, 0))
    best_move = moves[0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 100000
        if (nx, ny) in self_terr:
            score += 1000
        if (nx, ny) in opp_terr:
            score -= 5000

        d_opp = abs(nx - ox) + abs(ny - oy)
        score -= d_opp

        if unclaimed:
            best_dist = 10**18
            for ux, uy in unclaimed:
                dd = abs(nx - ux) + abs(ny - uy)
                if dd < best_dist:
                    best_dist = dd
                    if best_dist == 0:
                        break
            score -= best_dist

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
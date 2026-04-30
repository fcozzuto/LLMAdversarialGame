def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate each move by the best "denial/advantage" over all resources:
    # advantage = (opponent distance to resource) - (our distance to resource)
    # plus small tie-breakers to reduce dithering and keep distance from opponent.
    best_move = None
    best_score = -10**9
    best_adv = -10**9
    for dx, dy, nx, ny in legal:
        if resources:
            adv = -10**9
            for rx, ry in resources:
                our_d = manh(nx, ny, rx, ry)
                opp_d = manh(ox, oy, rx, ry)
                v = opp_d - our_d
                if v > adv:
                    adv = v
            # Prefer larger advantage; if tied, prefer getting closer to the nearest resource and farther from opponent.
            nearest = min(manh(nx, ny, rx, ry) for rx, ry in resources)
            opp_near = manh(nx, ny, ox, oy)
            score = adv * 1000 - nearest + opp_near * 0.01
        else:
            # No resources: move to maximize distance from opponent while avoiding obstacles
            dist_to_opp = manh(nx, ny, ox, oy)
            score = dist_to_opp
            adv = dist_to_opp
        # Deterministic tie-breaking: prefer staying closer to "lower dx, then lower dy" order.
        if score > best_score or (score == best_score and (adv > best_adv or (adv == best_adv and (dx, dy) < (best_move[0], best_move[1])))):
            best_score = score
            best_adv = adv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
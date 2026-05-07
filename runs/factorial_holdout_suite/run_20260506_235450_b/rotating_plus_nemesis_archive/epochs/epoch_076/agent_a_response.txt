def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    best_score = -10**18
    best_move = (0, 0)

    if resources:
        # Prefer immediate collection, then maximize lead in reaching resources.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = 0
            if (nx, ny) in res_set:
                score += 10**6
            # Evaluate best resource for us after moving, and how far opponent is from that same resource.
            for rx, ry in resources:
                self_d = md(nx, ny, rx, ry)
                opp_d = md(ox, oy, rx, ry)
                # Lead-based preference: smaller self_d, larger (opp_d - self_d).
                score += (opp_d - self_d) * 3 - self_d
            # Small tie-break to keep movement steady toward center of reachable space.
            score += -md(nx, ny, cx, cy)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    else:
        # No resources visible: move toward center while keeping distance advantage over opponent.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            self_to_center = md(nx, ny, cx, cy)
            self_to_opp = md(nx, ny, ox, oy)
            opp_to_center = md(ox, oy, cx, cy)
            # Prefer reducing our center distance; if equal, prefer keeping/creating distance from opponent.
            score = -self_to_center * 10 + (self_to_opp - opp_to_center)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
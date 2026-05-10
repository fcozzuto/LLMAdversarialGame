def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    if resources:
        targets = resources
    elif unclaimed:
        targets = unclaimed
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = [(w // 2, h // 2)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = {(0, 0): 0, (-1, 0): 1, (0, -1): 2, (1, 0): 3, (0, 1): 4, (-1, -1): 5, (1, -1): 6, (-1, 1): 7, (1, 1): 8}

    def man(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if self_terr and (nx, ny) not in self_terr and len(self_terr) > 0:
            pass

        d_self = man((nx, ny), (sx, sy))
        d_opp = man((nx, ny), (ox, oy))
        d_t = min(man((nx, ny), t) for t in targets) if targets else 0

        score = d_t * 10 + d_self - d_opp
        if best_score is None or score < best_score or (score == best_score and order[(dx, dy)] < order[best]):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
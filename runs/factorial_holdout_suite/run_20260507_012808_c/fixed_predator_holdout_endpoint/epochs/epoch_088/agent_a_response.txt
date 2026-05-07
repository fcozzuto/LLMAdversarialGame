def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = None

    opp_reach = []
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        opp_reach.append((d, rx, ry))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Favor grabbing/denying: maximize (opponent closeness - our next closeness),
        # and secondarily minimize our next distance and bias toward lower coordinates for determinism.
        best_adv = None
        best_selfd = None
        best_cell = None
        for od, rx, ry in opp_reach:
            selfd = cheb(nx, ny, rx, ry)
            adv = od - selfd
            if best_adv is None or (adv, -selfd, -(rx + ry), -rx, -ry) > (best_adv, -best_selfd, -(best_cell[0] + best_cell[1]), -best_cell[0], -best_cell[1]):
                best_adv, best_selfd, best_cell = adv, selfd, (rx, ry)

        # Extra push to immediately collect if standing on a resource.
        collect_bonus = 3 if best_cell in resources and best_selfd == 0 else 0
        key = (best_adv + collect_bonus, -best_selfd, -(best_cell[0] + best_cell[1]), -nx, -ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move
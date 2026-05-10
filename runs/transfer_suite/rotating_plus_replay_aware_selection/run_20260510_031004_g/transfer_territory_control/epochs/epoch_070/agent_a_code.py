def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        tx, ty = sx + dx, sy + dy
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        cell = (tx, ty)
        status = 0
        if cell in self_terr:
            status = 2
        elif cell in opp_terr:
            status = 4
        elif cell in unclaimed:
            status = 3

        center_bias = -(abs(tx - cx) + abs(ty - cy)) * 0.12
        my_adv = 0.0
        if cell in opp_terr:
            my_adv += 2.5
        elif cell in unclaimed:
            my_adv += 1.2
        elif cell in self_terr:
            my_adv += 0.2

        # If we can immediately touch opponent territory, value it.
        adj_opp = 0
        for adx, ady in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = tx + adx, ty + ady
            if inb(nx, ny) and (nx, ny) in opp_terr:
                adj_opp += 1
        adj_opp_val = adj_opp * 0.35

        # Prefer moving away from being stuck near opponent while contesting center.
        dist_opp = abs(tx - ox) + abs(ty - oy)
        dist_pen = dist_opp * 0.02

        score = status + center_bias + my_adv + adj_opp_val - dist_pen
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if isinstance(best_move, list) else [0, 0]
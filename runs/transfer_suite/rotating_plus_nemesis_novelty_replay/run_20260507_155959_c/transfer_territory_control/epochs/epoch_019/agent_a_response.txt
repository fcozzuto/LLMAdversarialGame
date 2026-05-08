def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0

    if opp_cells:
        ax = sum(x for x, _ in opp_cells) / len(opp_cells)
        ay = sum(y for _, y in opp_cells) / len(opp_cells)
        opp_center = (int(ax), int(ay))
    else:
        opp_center = (ox, oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**9)

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opppos = (ox, oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            continue
        status = 0
        if (nx, ny) in opp_cells:
            status = 5
        elif (nx, ny) in unclaimed:
            status = 2
        elif (nx, ny) in self_cells:
            status = 0
        else:
            status = 0

        away = dist(nx, ny, opp_center[0], opp_center[1])
        chase = -dist(nx, ny, opppos[0], opppos[1])
        edge = 0
        if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
            edge = 0.5

        score = status * 10 + away * 0.12 + chase * 0.08 + edge
        # Tie-break deterministically: prefer closer to center moves in fixed delta order already
        if score > best[1]:
            best = ([dx, dy], score)

    if best[0] is None:
        return [0, 0]
    return best[0]
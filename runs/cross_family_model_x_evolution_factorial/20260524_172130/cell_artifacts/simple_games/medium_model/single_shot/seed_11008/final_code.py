def choose_move(observation):
    # Robustly extract coordinates with defaults
    gw = observation.get('grid_width', 0)
    gh = observation.get('grid_height', 0)

    pos = observation.get('self_position', observation.get('self', {}))
    x = pos.get('x', 0) if isinstance(pos, dict) else 0
    y = pos.get('y', 0) if isinstance(pos, dict) else 0

    opp = observation.get('opponent_position', observation.get('opponent', {}))
    ox = opp.get('x', 0) if isinstance(opp, dict) else 0
    oy = opp.get('y', 0) if isinstance(opp, dict) else 0

    res = observation.get('resources', [])
    if not isinstance(res, list):
        res = []

    dx = 0
    dy = 0

    # 1) Move toward closest resource if any
    best = None
    bestd = None
    for r in res:
        if not isinstance(r, dict):
            continue
        rx = r.get('x', 0)
        ry = r.get('y', 0)
        d = abs(rx - x) + abs(ry - y)
        if bestd is None or d < bestd:
            bestd = d
            best = (rx, ry)
    if best is not None:
        rx, ry = best
        dx = 1 if rx > x else (-1 if rx < x else 0)
        dy = 1 if ry > y else (-1 if ry < y else 0)
        return [dx, dy]

    # 2) If opponent nearby, try to dodge slightly by moving away from them
    if (abs(ox - x) <= 1 and abs(oy - y) <= 1):
        dx = -1 if ox > x else (1 if ox < x else 0)
        dy = -1 if oy > y else (1 if oy < y else 0)
        return [dx, dy]

    # 3) Otherwise move toward center of grid deterministically
    cx = gw // 2
    cy = gh // 2
    dx = 1 if cx > x else (-1 if cx < x else 0)
    dy = 1 if cy > y else (-1 if cy < y else 0)
    return [dx, dy]

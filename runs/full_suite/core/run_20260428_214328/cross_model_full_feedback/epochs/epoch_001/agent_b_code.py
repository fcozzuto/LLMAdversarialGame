def choose_move(observation):
    # deterministic simple strategy: move toward nearest resource not occupied by obstacle or opponent,
    # but avoid stepping into opponent's position. If no resource available, approach opponent to contest.
    x, y = observation['self_position']
    oppx, oppy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    # helper to compute distance
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    # build set for quick checks
    occ = {tuple(p) for p in obstacles}
    if resources:
        # pick closest resource not blocked by obstacle; if multiple, pick deterministic by coords
        best = None
        bestd = 10**9
        for r in resources:
            rx, ry = r
            if (rx, ry) in occ:
                continue
            d = dist((x, y), (rx, ry))
            if d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        if best is not None:
            rx, ry = best
            dx = 0
            dy = 0
            if rx > x: dx = 1
            elif rx < x: dx = -1
            if ry > y: dy = 1
            elif ry < y: dy = -1
            # ensure not moving into opponent
            if (x+dx, y+dy) == (oppx, oppy):
                dx, dy = 0, 0
            # ensure within grid
            nx, ny = x+dx, y+dy
            if 0 <= nx < observation['grid_width'] and 0 <= ny < observation['grid_height']:
                return [dx, dy]
    # fallback: move toward opponent to contest if safe
    dx = 0
    dy = 0
    if oppx > x: dx = 1
    elif oppx < x: dx = -1
    if oppy > y: dy = 1
    elif oppy < y: dy = -1
    nx, ny = x+dx, y+dy
    # avoid obstacles and staying in place ruled acceptable; if would collide with obstacle or out of bounds, stay
    if (nx, ny) in {tuple(o) for o in obstacles} or not (0 <= nx < observation['grid_width'] and 0 <= ny < observation['grid_height']):
        dx, dy = 0, 0
    # also avoid moving into opponent's current square
    if (x+dx, y+dy) == (oppx, oppy):
        dx, dy = 0, 0
    return [dx, dy]
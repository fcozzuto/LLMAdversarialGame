def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    evader = ("evader" in roles) and ("purs" not in roles)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    best = None
    bestm = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        # target: pursue (min dist) or evade (max dist)
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        center2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        if evader:
            # primary: maximize distance; secondary: move away from edges by preferring center
            key = (dist2, -center2, -abs(ox - nx) - abs(oy - ny), dx, dy)
        else:
            # primary: minimize distance; secondary: prefer center to avoid corner traps
            key = (-dist2, -center2, abs(ox - nx) + abs(oy - ny), dx, dy)

        if best is None or key > best:
            best = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]
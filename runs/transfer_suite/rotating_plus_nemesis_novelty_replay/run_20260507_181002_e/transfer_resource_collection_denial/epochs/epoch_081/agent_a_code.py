def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Look for the most favorable resource "contest" next turn.
        # Score components: maximize (opp_d - self_d) over all resources,
        # then minimize self distance to that resource, then prefer "safe" moves
        # that keep us away from immediate opponent advantage zones.
        best_adv = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv, best_sd = adv, sd

        # Additional tie-break: maximize immediate progress to the closest resource.
        closest = best_sd
        opp_closest = min(manh(ox, oy, rx, ry) for rx, ry in resources)
        # Encourage taking resources sooner than opponent; discourage if opponent already closer.
        key = (best_adv, -closest, opp_closest - best_sd, -manh(nx, ny, w - 1 if sy < h//2 else 0, h - 1 if sx > w//2 else 0))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
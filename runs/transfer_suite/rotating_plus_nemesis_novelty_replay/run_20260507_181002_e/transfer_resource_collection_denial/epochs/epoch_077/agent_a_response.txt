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

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # One-step contest heuristic:
        # maximize advantage (opp_d - self_d), then prefer closer self, then farther opp.
        best_adv = -10**18
        best_self_d = 10**9
        best_opp_d = -1
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and (self_d < best_self_d or (self_d == best_self_d and opp_d > best_opp_d))):
                best_adv, best_self_d, best_opp_d = adv, self_d, opp_d

        # Small bias: if multiple resources yield similar advantage, choose the move that improves the current-nearest target.
        # Deterministic tie-break favors progressing away from current position to avoid "no gain" repeats.
        score = (best_adv, -best_self_d, best_opp_d, -(abs(nx - sx) + abs(ny - sy)))
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]
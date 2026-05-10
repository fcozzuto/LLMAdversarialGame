def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    if not unclaimed and not oppT:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaker: lower-index first in deltas list
    best = deltas[4]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 6.0
        elif (nx, ny) in oppT:
            score += 3.5
        elif (nx, ny) in selfT:
            score += 1.0
        else:
            score += 0.2  # empty/unknown

        # Frontier pressure: prefer stepping near unclaimed
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in unclaimed:
                    near += 1
        score += 1.2 * near

        # Center bias (helps deterministic expansion)
        dist_center = abs(nx - cx) + abs(ny - cy)
        score += -0.03 * dist_center

        # Keep distance from opponent territory center to avoid getting wiped
        op_cells = list(oppT)
        if op_cells:
            oxm = sum(p[0] for p in op_cells) / len(op_cells)
            oym = sum(p[1] for p in op_cells) / len(op_cells)
            score += -0.02 * (abs(nx - oxm) + abs(ny - oym))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
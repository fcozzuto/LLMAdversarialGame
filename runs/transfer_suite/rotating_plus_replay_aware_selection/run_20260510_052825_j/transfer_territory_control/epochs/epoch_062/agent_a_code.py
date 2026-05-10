def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = -10**18

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 7.0
        elif (nx, ny) in oppT:
            score += 4.0
        elif (nx, ny) in selfT:
            score += 1.5
        else:
            score += 0.1

        # Frontier pressure: prefer moves that increase adjacent unclaimed capture
        adj_u = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in unclaimed:
                    adj_u += 1
        score += adj_u * 1.1

        # Center bias to avoid drifting to corners too late
        dist_c = abs(nx - cx) + abs(ny - cy)
        score -= dist_c * 0.03

        # Small bias towards increasing controlled area and away from opp blobs
        adj_opp = 0
        adj_self = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in oppT:
                    adj_opp += 1
                if inb(tx, ty) and (tx, ty) in selfT:
                    adj_self += 1
        score += adj_self * 0.15
        score -= adj_opp * 0.05

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]
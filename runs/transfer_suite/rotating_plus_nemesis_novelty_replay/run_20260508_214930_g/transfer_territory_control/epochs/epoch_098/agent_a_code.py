def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Distances (Manhattan)
        d_opp = abs(nx - ox) + abs(ny - oy)
        if unclaimed:
            d_un = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed)
        else:
            d_un = 10**9
        if resources:
            d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            d_res = 10**9

        score = 0
        if (nx, ny) in unclaimed:
            score += 1000
        if (nx, ny) in resources:
            score += 500
        score += (0 if d_un >= 10**8 else 200 - d_un)
        score += (0 if d_res >= 10**8 else 120 - d_res)
        score += d_opp * 2  # prefer being farther from opponent

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
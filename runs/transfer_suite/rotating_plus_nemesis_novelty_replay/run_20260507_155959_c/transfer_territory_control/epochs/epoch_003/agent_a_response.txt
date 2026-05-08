def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    selfT = set(tuple(p) for p in observation.get("self_territory", []))
    oppT = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None  # (score, -dist_to_opp, -dist_to_unclaimed, dx, dy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            nxt = (nx, ny)
            dist_opp = abs(nx - ox) + abs(ny - oy)

            if unclaimed:
                dist_un = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed)
            else:
                dist_un = 999

            score = 0
            if nxt in oppT:
                score += 4
                # discourage easy counterclaim by avoiding deep dives; prefer capturing that pushes away
                score -= 0.02 * dist_opp
            elif nxt in unclaimed:
                score += 3
                score -= 0.01 * dist_opp
            elif nxt in selfT:
                score += 1
                score -= 0.005 * dist_opp
            else:
                score += 0

            # avoid getting boxed in: count obstacle adjacency (prefer fewer)
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    xx, yy = nx + ax, ny + ay
                    if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obstacles:
                        adj_obs += 1
            score -= 0.02 * adj_obs

            cand = (score, -dist_opp, -dist_un, dx, dy)
            if best is None or cand > best:
                best = cand

    if best is not None:
        return [best[3], best[4]]

    # if all moves invalid, stay still
    return [0, 0]
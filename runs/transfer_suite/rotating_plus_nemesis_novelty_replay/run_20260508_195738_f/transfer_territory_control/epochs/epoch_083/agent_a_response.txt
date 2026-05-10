def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    opp = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selft = set(tuple(p) for p in (observation.get("self_territory") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Nearest targets we can expand into
    if unclaimed:
        un_list = list(unclaimed)
        closest_un = min(un_list, key=lambda p: dist((sx, sy), p))
    else:
        closest_un = None

    # Opponent proximity: if close, guard/space
    opp_list = list(opp)
    closest_opp = None
    if opp_list:
        closest_opp = min(opp_list, key=lambda p: dist((sx, sy), p))

    best = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Proxy score for the landing cell
        cell = 0
        if (nx, ny) in selft:
            cell += 1
        if (nx, ny) in unclaimed:
            cell += 6
        if (nx, ny) in opp:
            cell -= 20  # entering opponent territory is risky vs counterclaim

        # If close to opponent territory, prefer moving away
        if closest_opp is not None:
            d0 = dist((sx, sy), closest_opp)
            d1 = dist((nx, ny), closest_opp)
            cell += (d1 - d0) * 2

        # Prefer moving toward a good unclaimed expansion target
        if closest_un is not None:
            d0 = dist((sx, sy), closest_un)
            d1 = dist((nx, ny), closest_un)
            cell += (d0 - d1) * 1.8

            # Extra shaping: don't step into cells that are "inside" opponent clusters
            if (nx, ny) not in unclaimed and closest_opp is not None:
                # count adjacent opponent cells
                adj_opp = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        if ax == 0 and ay == 0:
                            continue
                        if (nx + ax, ny + ay) in opp:
                            adj_opp += 1
                cell -= adj_opp * 1.2

        # Mild preference to expand along edges when no clear target
        if closest_un is None:
            if nx in (0, w - 1) or ny in (0, h - 1):
                cell += 2

        if cell > best:
            best = cell
            best_move = [dx, dy]

    return best_move
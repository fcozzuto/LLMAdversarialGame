def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    self_terr = set(tuple(map(int, p)) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(map(int, p)) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(map(int, p)) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break
    t = int(observation.get("turn_index", 0) or 0)

    best = [0, 0]
    best_score = -10**9
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -10**8
        else:
            # Encourage expansion and opportunistic stealing from opponent territory
            if (nx, ny) in opp_terr:
                sc = 200
            elif (nx, ny) in unclaimed:
                sc = 60
            elif (nx, ny) in self_terr:
                sc = 10
            else:
                sc = 0
            # Prefer moving toward opponent boundary (cells adjacent to their territory)
            near_opp = 0
            for adx, ady in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
                ax, ay = nx + adx, ny + ady
                if inside(ax, ay) and (ax, ay) in opp_terr:
                    near_opp += 1
            sc += 7 * near_opp
            # Avoid corners/obstacle clutter by penalizing proximity to obstacles
            prox = 0
            for adx, ady in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
                ax, ay = nx + adx, ny + ady
                if inside(ax, ay) and (ax, ay) in obstacles:
                    prox += 1
            sc -= 15 * prox
            # Mild preference for direction that reduces distance to opponent "center of mass"
            if opp_terr:
                cx = sum(p[0] for p in opp_terr) / len(opp_terr)
                cy = sum(p[1] for p in opp_terr) / len(opp_terr)
                d0 = abs(sx - cx) + abs(sy - cy)
                d1 = abs(nx - cx) + abs(ny - cy)
                sc += int((d0 - d1) * 4)
            # Deterministic tie-break
            sc += -i * 0.001 + ((t + i) % 2) * 0.0001
        if sc > best_score:
            best_score = sc
            best = [dx, dy]
    return [int(best[0]), int(best[1])]
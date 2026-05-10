def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    oppx, oppy = observation["opponent_position"]
    opp_dist = abs(sx - oppx) + abs(sy - oppy)

    best_move = [0, 0]
    best_score = -10**9

    # Light global bias toward unclaimed closer to opponent, if any exist.
    if unclaimed:
        # deterministic: choose a "best" unclaimed by score: closer to opponent, then farther from self
        best_global = None
        best_global_key = None
        for ux, uy in unclaimed:
            if (ux, uy) in obstacles:
                continue
            key = (abs(ux - oppx) + abs(uy - oppy), -(abs(ux - sx) + abs(uy - sy)), ux, uy)
            if best_global_key is None or key < best_global_key:
                best_global_key = key
                best_global = (ux, uy)
        gx, gy = best_global
    else:
        gx, gy = None, None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        target = (nx, ny)
        a_self = adj_count(nx, ny, self_t)
        a_opp = adj_count(nx, ny, opp_t)
        dist_to_opp = abs(nx - oppx) + abs(ny - oppy)

        score = 0
        if target in self_t:
            score += 2 + a_self - a_opp
        elif target in opp_t:
            # strong payoff on flip; prefer cells adjacent to our territory and not deeply surrounded by theirs
            score += 15 + 3 * a_self - 2 * a_opp
            score += 1 if dist_to_opp < opp_dist else 0
        else:
            # claim unclaimed: prefer expanding frontier toward opponent
            if target in unclaimed:
                score += 6 + 2 * a_self + a_opp
                score += 2 if dist_to_opp <= opp_dist else 0
            else:
                # entering neither territory nor unclaimed shouldn't exist, but keep safe
                score += 1

            # global directional bias toward the selected unclaimed goal
            if gx is not None:
                gcur = abs(sx - gx) + abs(sy - gy)
                gnext = abs(nx - gx) + abs(ny - gy)
                score += 2 if gnext < gcur else (-1 if gnext > gcur else 0)

            # avoid getting swallowed: if adjacent mostly to opponent and no adjacency to self, be cautious
            if a_opp >= a_self + 2 and a_self == 0:
                score -= 5

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_score < -3:
        return [0, 0]
    return best_move
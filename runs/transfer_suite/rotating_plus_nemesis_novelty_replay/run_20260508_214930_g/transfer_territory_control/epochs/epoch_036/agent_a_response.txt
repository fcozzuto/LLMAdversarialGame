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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in sset:
                    c += 1
        return c

    def dist_to_set(x, y, sset):
        if not sset:
            return 10**9
        best = 10**9
        for (tx, ty) in sset:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    # Prefer expanding from our boundary, but avoid getting trapped near opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        is_opp = (nx, ny) in opp_t
        is_self = (nx, ny) in self_t
        is_un = (nx, ny) in unclaimed

        if is_opp:
            # Only enter opponent territory if it improves expansion potential significantly.
            opp_adj = adj_count(nx, ny, opp_t)
            self_adj = adj_count(nx, ny, self_t)
            val = -50 + self_adj * 6 + (is_un * 3) - opp_adj * 2
        else:
            self_adj = adj_count(nx, ny, self_t)
            opp_adj = adj_count(nx, ny, opp_t)
            un_adj = adj_count(nx, ny, unclaimed)

            # Push towards unclaimed "frontier" cells but keep a safety margin from opponent.
            if unclaimed:
                d_un = dist_to_set(nx, ny, unclaimed)
            else:
                d_un = 50

            # Safety: if we are near opponent, prefer staying or pushing away from them.
            d_opp = dist_to_set(nx, ny, opp_t) if opp_t else 50
            safety = d_opp * 1.2

            # Encourage claiming new territory: unclaimed is a direct target, otherwise extend self boundary.
            val = (self_adj * 8) + (un_adj * 2.5) + (is_un * 10) + safety - (opp_adj * 6) - d_un * 0.7
            if is_self:
                val -= 1.5  # discourage pure stalling on already-owned cells

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
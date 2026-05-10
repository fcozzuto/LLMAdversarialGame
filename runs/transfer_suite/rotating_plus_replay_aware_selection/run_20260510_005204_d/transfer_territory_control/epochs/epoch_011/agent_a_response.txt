def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    t = int(observation.get("turn_index", 0))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    un_set = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    self_tc = int(observation.get("self_territory_count", 0))
    opp_tc = int(observation.get("opponent_territory_count", 0))

    # Leader bonus only applies if sole leader; we approximate with tie/near-leader.
    leader_bonus = 0.5 if (t % 10 == 0 and self_tc >= opp_tc) else 0.0

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        d_opp = dist(nx, ny, ox, oy)

        if (nx, ny) in opp_set:
            # Direct counterclaim: high value, but only if it brings us closer.
            score += 26.0 + leader_bonus
            score += 0.9 * (dist(sx, sy, ox, oy) - d_opp)  # approach opponent
            score -= 0.35 * d_opp
        elif (nx, ny) in un_set:
            # Territory expansion: claim unclaimed, prefer moving toward opponent side.
            score += 14.0
            score += 0.6 * (dist(sx, sy, ox, oy) - d_opp)
            score -= 0.15 * d_opp
        elif (nx, ny) in self_set:
            # Staying/continuing: slightly prefer advancing toward opponent.
            score += 6.0
            score += 0.25 * (dist(sx, sy, ox, oy) - d_opp)
        else:
            # Should be rare: untracked/unclaimed; neutral but avoid random drift.
            score += 2.0 - 0.05 * d_opp

        # Avoid walking into opponent if we're already behind: try to widen via unclaimed.
        if self_tc < opp_tc:
            if (nx, ny) in opp_set:
                score -= 4.0
            else:
                score += 1.5

        # Prefer moves that increase "frontier": cells adjacent to unclaimed/opp.
        frontier = 0
        for adx, ady in dirs:
            ax2, ay2 = nx + adx, ny + ady
            if not inb(ax2, ay2) or (ax2, ay2) in obstacles:
                continue
            if (ax2, ay2) in un_set:
                frontier += 2
            elif (ax2, ay2) in opp_set:
                frontier += 1
        score += 0.9 * frontier

        # Deterministic tie-breaker: lower dx/dy lexicographic preference towards opponent roughly.
        if score > best_val or (score == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
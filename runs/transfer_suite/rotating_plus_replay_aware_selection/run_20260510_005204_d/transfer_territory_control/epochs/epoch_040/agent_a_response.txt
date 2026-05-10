def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    neigh8 = moves
    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def count_adj_unclaimed(x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def frontier_bonus_to_unclaimed(x, y):
        # encourages stepping adjacent to frontier cells
        b = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                # prefer unclaimed that are also adjacent to our territory (clear expansion line)
                adj_self = 0
                for ddx, ddy in neigh4:
                    ax, ay = nx + ddx, ny + ddy
                    if inb(ax, ay) and (ax, ay) in self_terr:
                        adj_self += 1
                b += 1 + (2 if adj_self else 0)
        return b

    def block_opponent_if_possible(x, y):
        # if stepping into/near opponent territory, estimate flip potential by proximity
        if (x, y) in opp_terr:
            return 50
        b = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                b += 8
        return b

    def bias_away_from_neutral_corner_trap(x, y):
        # deterministic "sweep": after early turns, favor the center band
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        # less distance to center == better; small tie-break
        return -((x - cx) * (x - cx) + (y - cy) * (y - cy)) * (1.0 if observation["turn_index"] > 12 else 0.3)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 30 + 2 * count_adj_unclaimed(nx, ny) + 3 * frontier_bonus_to_unclaimed(nx, ny)
        elif (nx, ny) in opp_terr:
            score += 28 + 2 * count_adj_unclaimed(nx, ny) + block_opponent_if_possible(nx, ny)
        elif (nx, ny) in self_terr:
            score += 2 * count_adj_unclaimed(nx, ny)

        score += block_opponent_if_possible(nx, ny)

        # prevent getting stuck near borders: slight preference for staying inside
        score += bias_away_from_neutral_corner_trap(nx, ny)

        # tie-break deterministically: prefer (0,0), then lowest dx, then lowest dy
        tie = (0 if (dx == 0 and dy == 0) else 1, abs(dx) + abs(dy), dx, dy)

        if best_score is None or score > best_score or (score == best_score and tie < best_tie):
            best_score = score
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
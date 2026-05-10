def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_terr = set(tuple(p) for p in observation.get("self_territory", []))
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    # If there are no unclaimed cells, just try to approach/steal.
    any_unclaimed = len(unclaimed) > 0

    best = None
    best_score = None

    # Deterministic tie-breaker order
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        cell = (nx, ny)

        # Immediate territory control value
        if cell in opp_terr:
            score += 8.0  # aggressive stealing (flipping on entry is enabled)
        elif cell in unclaimed:
            score += 5.0  # expand into neutral
        elif cell in self_terr:
            score += 1.0  # safe consolidation

        # Encourage boundary play: reward moving closer to unclaimed/opponent border
        # Use Chebyshev distance for grid with diagonals allowed.
        if any_unclaimed:
            # Choose nearest unclaimed in a deterministic way by approximating via min over a small subset
            # (still deterministic because we iterate sorted).
            nearest = None
            for (ux, uy) in sorted(unclaimed)[:40]:
                d = max(abs(ux - nx), abs(uy - ny))
                if nearest is None or d < nearest:
                    nearest = d
                    if d == 0:
                        break
            if nearest is not None:
                score += 2.5 / (1 + nearest)
        # Also push toward opponent when not much to expand
        d_opp = max(abs(nx - ox), abs(ny - oy))
        score += 1.5 / (1 + d_opp)

        # Slight penalty for staying too long if expansion exists
        if dx == 0 and dy == 0:
            score -= (2.0 if any_unclaimed else 0.5)

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
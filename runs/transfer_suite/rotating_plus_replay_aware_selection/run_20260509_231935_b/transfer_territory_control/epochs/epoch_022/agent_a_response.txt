def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []))
    self_territory = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
    opponent_territory = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position") or (None, None)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x, y, a, b):
        return abs(x - a) + abs(y - b)

    # Frontier bias: prefer unclaimed adjacent to our territory.
    frontier = set()
    for (x, y) in self_territory:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))

    best = [0, 0]
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue

            val = 0.0

            if (nx, ny) in self_territory:
                val += 0.2
            elif (nx, ny) in opponent_territory:
                # Favor flipping opponent territory, especially near them.
                if ox is None:
                    val += 80
                else:
                    val += 120 - 2.5 * md(nx, ny, ox, oy)
            elif (nx, ny) in unclaimed:
                # Expansion: prioritize frontier; also avoid running straight into their center.
                val += 18 if (nx, ny) in frontier else 8
                if ox is not None:
                    val += 1.5 * md(nx, ny, ox, oy)  # generally move away unless capturing
            else:
                val += 0.0

            # Mild preference to keep distance from opponent unless capturing.
            if ox is not None and (nx, ny) not in opponent_territory:
                val += 0.5 * md(nx, ny, ox, oy)

            if val > best_val:
                best_val = val
                best = [dx, dy]

    return best
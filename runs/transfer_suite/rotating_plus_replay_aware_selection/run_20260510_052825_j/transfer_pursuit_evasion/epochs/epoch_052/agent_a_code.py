def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if self_is_evader:
        # Move away from opponent while pushing toward the farthest corner (with obstacle avoidance).
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer increasing distance to opponent and also increasing distance to opponent along corner direction.
            score = dist2(nx, ny, ox, oy)
            score += 0.25 * dist2(nx, ny, tx, ty)
            # Penalize proximity to obstacles (local only).
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        score -= 3.0
            # Deterministic tie-break: lexicographic by move preference order already fixed by deltas.
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        # Pursuer: reduce distance to opponent with obstacle avoidance; use corner bias to avoid getting stuck.
        tx, ty = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            score = -dist2(nx, ny, ox, oy)  # maximize negative => minimize distance
            score -= 0.1 * dist2(nx, ny, tx, ty)  # slight bias toward that corner region
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        score -= 4.0
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is None:
            return [0, 0]
        return [best[0], best[1]]